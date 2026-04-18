import React from 'react';
import FormattedAIText from './FormattedAIText';
import IPCMetadataPanel from './IPCMetadataPanel';
import SpeechPlaybackControls from './SpeechPlaybackControls';
import { formatPunishment } from '../ipcUtils';

const containsPredictedCharges = (text) => (
  typeof text === 'string' && /predicted\s*charges\s*:/i.test(text)
);

const ExpandableIPCItem = ({ title, subtitle, children, accentClassName = 'border-gray-200 bg-white' }) => (
  <details className={`rounded-md border p-3 ${accentClassName}`}>
    <summary className="cursor-pointer list-none">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="font-medium text-gray-900">{title}</div>
          {subtitle ? <div className="mt-1 text-sm text-gray-600">{subtitle}</div> : null}
        </div>
        <span className="text-xs font-medium text-gray-500">Show details</span>
      </div>
    </summary>
    <div className="mt-3">{children}</div>
  </details>
);

const AIResponseDetails = ({
  responseText,
  charges = [],
  matchedSections = [],
  structuredResponse = null,
  language = 'english',
  responseContainerClassName = 'bg-blue-50 p-4 rounded-lg',
  matchedSectionsContainerClassName = 'bg-amber-50 p-4 rounded-lg',
}) => {
  const severity = structuredResponse?.severity;
  const ipcSections = structuredResponse?.ipc_sections || [];
  const displayCharges = structuredResponse?.charges?.length ? structuredResponse.charges : charges;
  const displayMatchedSections = ipcSections.length > 0
    ? ipcSections.map((item) => item.section_data).filter(Boolean)
    : matchedSections;
  const steps = structuredResponse?.steps || [];
  const evidenceChecklist = structuredResponse?.evidence_checklist || [];
  const courtFlow = structuredResponse?.court_flow;
  const showLegacyText = !structuredResponse;

  return (
    <div className="space-y-4">
      <div className={responseContainerClassName}>
        <h4 className="mb-2 font-medium text-gray-900">{structuredResponse ? 'Case Overview' : 'AI Response:'}</h4>
        {showLegacyText ? (
          <FormattedAIText text={responseText} />
        ) : (
          <div className="space-y-3 text-sm text-gray-700">
            <p>{structuredResponse.understanding}</p>
            {structuredResponse.tips?.length > 0 ? (
              <div>
                <p className="font-medium text-gray-900">Tips</p>
                <ul className="mt-1 list-disc space-y-1 pl-5">
                  {structuredResponse.tips.map((tip, index) => (
                    <li key={`${tip}-${index}`}>{tip}</li>
                  ))}
                </ul>
              </div>
            ) : null}
            {structuredResponse.donts?.length > 0 ? (
              <div>
                <p className="font-medium text-gray-900">Don'ts</p>
                <ul className="mt-1 list-disc space-y-1 pl-5">
                  {structuredResponse.donts.map((item, index) => (
                    <li key={`${item}-${index}`}>{item}</li>
                  ))}
                </ul>
              </div>
            ) : null}
          </div>
        )}
        <SpeechPlaybackControls
          text={structuredResponse?.audio_text || structuredResponse?.understanding || responseText}
          language={language}
        />
      </div>

      {structuredResponse ? (
        <>
          <div className="grid gap-4 lg:grid-cols-2">
            <div className="rounded-lg border border-rose-200 bg-rose-50 p-4">
              <h4 className="mb-2 font-medium text-gray-900">Severity</h4>
              <p className="text-sm font-semibold text-rose-700">{severity?.label || 'LOW'}</p>
              <p className="mt-2 text-sm text-gray-700">{severity?.urgency_note}</p>
            </div>
            <div className="rounded-lg border border-sky-200 bg-sky-50 p-4">
              <h4 className="mb-2 font-medium text-gray-900">Persona</h4>
              <p className="text-sm text-gray-700">{structuredResponse.persona_note}</p>
            </div>
          </div>

          {steps.length > 0 ? (
            <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4">
              <h4 className="mb-3 font-medium text-gray-900">Step-by-Step Action Plan</h4>
              <ol className="space-y-2 text-sm text-gray-700">
                {steps.map((step, index) => (
                  <li key={`${step.title}-${index}`}>
                    <span className="font-semibold text-gray-900">{index + 1}. {step.title}</span> {step.detail}
                  </li>
                ))}
              </ol>
            </div>
          ) : null}

          {evidenceChecklist.length > 0 ? (
            <div className="rounded-lg border border-violet-200 bg-violet-50 p-4">
              <h4 className="mb-3 font-medium text-gray-900">Evidence Checklist</h4>
              <ul className="list-disc space-y-1 pl-5 text-sm text-gray-700">
                {evidenceChecklist.map((item, index) => (
                  <li key={`${item}-${index}`}>{item}</li>
                ))}
              </ul>
            </div>
          ) : null}

          {courtFlow && Object.keys(courtFlow).length > 0 ? (
            <div className="rounded-lg border border-orange-200 bg-orange-50 p-4">
              <h4 className="mb-3 font-medium text-gray-900">Court Flow Prediction</h4>
              <p className="text-sm text-gray-700">
                <span className="font-semibold">Timeline:</span> {courtFlow.timeline_estimate}
              </p>
              <div className="mt-3 grid gap-3 lg:grid-cols-2">
                <div>
                  <p className="text-sm font-semibold text-gray-900">Stages</p>
                  <ul className="mt-1 list-disc space-y-1 pl-5 text-sm text-gray-700">
                    {(courtFlow.legal_stages || []).map((stage, index) => (
                      <li key={`${stage.stage}-${index}`}>{stage.stage}: {stage.detail}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <p className="text-sm font-semibold text-gray-900">Possible Outcomes</p>
                  <ul className="mt-1 list-disc space-y-1 pl-5 text-sm text-gray-700">
                    {(courtFlow.possible_outcomes || []).map((item, index) => (
                      <li key={`${item}-${index}`}>{item}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          ) : null}

          {structuredResponse.complaint_draft ? (
            <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
              <h4 className="mb-2 font-medium text-gray-900">FIR Complaint Draft</h4>
              <pre className="whitespace-pre-wrap font-sans text-sm text-gray-700">{structuredResponse.complaint_draft}</pre>
            </div>
          ) : null}
        </>
      ) : null}

      {displayCharges && displayCharges.length > 0 && !containsPredictedCharges(responseText) ? (
        <div className="rounded-lg bg-green-50 p-4">
          <h4 className="mb-3 font-medium text-gray-900">Predicted Charges</h4>
          <div className="space-y-3">
            {displayCharges.map((charge, index) => (
              <ExpandableIPCItem
                key={`${charge.section}-${index}`}
                title={`Section ${charge.section}: ${charge.title}`}
                subtitle={`Confidence ${(charge.confidence * 100).toFixed(1)}%${charge.punishment ? ` • ${formatPunishment(charge.punishment)}` : ''}`}
                accentClassName="border-green-200 bg-white"
              >
                <IPCMetadataPanel
                  section={{
                    ...charge,
                    section_number: charge.section
                  }}
                  compact
                />
              </ExpandableIPCItem>
            ))}
          </div>
        </div>
      ) : null}

      {displayMatchedSections && displayMatchedSections.length > 0 ? (
        <div className={matchedSectionsContainerClassName}>
          <h4 className="mb-3 font-medium text-gray-900">Referenced IPC Sections</h4>
          <div className="space-y-3">
            {displayMatchedSections.map((section, index) => (
              <ExpandableIPCItem
                key={`${section.section_number}-${index}`}
                title={`Section ${section.section_number}: ${section.title}`}
                subtitle={section.description || 'Open to view IPC details'}
                accentClassName="border-amber-200 bg-white"
              >
                <IPCMetadataPanel section={section} compact />
              </ExpandableIPCItem>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
};

export default AIResponseDetails;
